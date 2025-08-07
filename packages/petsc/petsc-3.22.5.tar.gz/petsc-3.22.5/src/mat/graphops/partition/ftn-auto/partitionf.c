#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* partition.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioninggettype_ MATPARTITIONINGGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioninggettype_ matpartitioninggettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningsetnparts_ MATPARTITIONINGSETNPARTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningsetnparts_ matpartitioningsetnparts
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningapplynd_ MATPARTITIONINGAPPLYND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningapplynd_ matpartitioningapplynd
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningapply_ MATPARTITIONINGAPPLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningapply_ matpartitioningapply
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningimprove_ MATPARTITIONINGIMPROVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningimprove_ matpartitioningimprove
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningviewimbalance_ MATPARTITIONINGVIEWIMBALANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningviewimbalance_ matpartitioningviewimbalance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningsetadjacency_ MATPARTITIONINGSETADJACENCY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningsetadjacency_ matpartitioningsetadjacency
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningdestroy_ MATPARTITIONINGDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningdestroy_ matpartitioningdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningsetuseedgeweights_ MATPARTITIONINGSETUSEEDGEWEIGHTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningsetuseedgeweights_ matpartitioningsetuseedgeweights
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioninggetuseedgeweights_ MATPARTITIONINGGETUSEEDGEWEIGHTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioninggetuseedgeweights_ matpartitioninggetuseedgeweights
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningcreate_ MATPARTITIONINGCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningcreate_ matpartitioningcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningviewfromoptions_ MATPARTITIONINGVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningviewfromoptions_ matpartitioningviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningview_ MATPARTITIONINGVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningview_ matpartitioningview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningsettype_ MATPARTITIONINGSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningsettype_ matpartitioningsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningsetfromoptions_ MATPARTITIONINGSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningsetfromoptions_ matpartitioningsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpartitioningsetnumbervertexweights_ MATPARTITIONINGSETNUMBERVERTEXWEIGHTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpartitioningsetnumbervertexweights_ matpartitioningsetnumbervertexweights
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matpartitioninggettype_(MatPartitioning partitioning,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(partitioning);
*ierr = MatPartitioningGetType(
	(MatPartitioning)PetscToPointer((partitioning) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  matpartitioningsetnparts_(MatPartitioning part,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningSetNParts(
	(MatPartitioning)PetscToPointer((part) ),*n);
}
PETSC_EXTERN void  matpartitioningapplynd_(MatPartitioning matp,IS *partitioning, int *ierr)
{
CHKFORTRANNULLOBJECT(matp);
PetscBool partitioning_null = !*(void**) partitioning ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(partitioning);
*ierr = MatPartitioningApplyND(
	(MatPartitioning)PetscToPointer((matp) ),partitioning);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! partitioning_null && !*(void**) partitioning) * (void **) partitioning = (void *)-2;
}
PETSC_EXTERN void  matpartitioningapply_(MatPartitioning matp,IS *partitioning, int *ierr)
{
CHKFORTRANNULLOBJECT(matp);
PetscBool partitioning_null = !*(void**) partitioning ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(partitioning);
*ierr = MatPartitioningApply(
	(MatPartitioning)PetscToPointer((matp) ),partitioning);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! partitioning_null && !*(void**) partitioning) * (void **) partitioning = (void *)-2;
}
PETSC_EXTERN void  matpartitioningimprove_(MatPartitioning matp,IS *partitioning, int *ierr)
{
CHKFORTRANNULLOBJECT(matp);
PetscBool partitioning_null = !*(void**) partitioning ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(partitioning);
*ierr = MatPartitioningImprove(
	(MatPartitioning)PetscToPointer((matp) ),partitioning);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! partitioning_null && !*(void**) partitioning) * (void **) partitioning = (void *)-2;
}
PETSC_EXTERN void  matpartitioningviewimbalance_(MatPartitioning matp,IS partitioning, int *ierr)
{
CHKFORTRANNULLOBJECT(matp);
CHKFORTRANNULLOBJECT(partitioning);
*ierr = MatPartitioningViewImbalance(
	(MatPartitioning)PetscToPointer((matp) ),
	(IS)PetscToPointer((partitioning) ));
}
PETSC_EXTERN void  matpartitioningsetadjacency_(MatPartitioning part,Mat adj, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
CHKFORTRANNULLOBJECT(adj);
*ierr = MatPartitioningSetAdjacency(
	(MatPartitioning)PetscToPointer((part) ),
	(Mat)PetscToPointer((adj) ));
}
PETSC_EXTERN void  matpartitioningdestroy_(MatPartitioning *part, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(part);
 PetscBool part_null = !*(void**) part ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningDestroy(part);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! part_null && !*(void**) part) * (void **) part = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(part);
 }
PETSC_EXTERN void  matpartitioningsetuseedgeweights_(MatPartitioning part,PetscBool *use_edge_weights, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningSetUseEdgeWeights(
	(MatPartitioning)PetscToPointer((part) ),*use_edge_weights);
}
PETSC_EXTERN void  matpartitioninggetuseedgeweights_(MatPartitioning part,PetscBool *use_edge_weights, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningGetUseEdgeWeights(
	(MatPartitioning)PetscToPointer((part) ),use_edge_weights);
}
PETSC_EXTERN void  matpartitioningcreate_(MPI_Fint * comm,MatPartitioning *newp, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(newp);
 PetscBool newp_null = !*(void**) newp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newp);
*ierr = MatPartitioningCreate(
	MPI_Comm_f2c(*(comm)),newp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newp_null && !*(void**) newp) * (void **) newp = (void *)-2;
}
PETSC_EXTERN void  matpartitioningviewfromoptions_(MatPartitioning A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = MatPartitioningViewFromOptions(
	(MatPartitioning)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  matpartitioningview_(MatPartitioning part,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
CHKFORTRANNULLOBJECT(viewer);
*ierr = MatPartitioningView(
	(MatPartitioning)PetscToPointer((part) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  matpartitioningsettype_(MatPartitioning part,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(part);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = MatPartitioningSetType(
	(MatPartitioning)PetscToPointer((part) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  matpartitioningsetfromoptions_(MatPartitioning part, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = MatPartitioningSetFromOptions(
	(MatPartitioning)PetscToPointer((part) ));
}
PETSC_EXTERN void  matpartitioningsetnumbervertexweights_(MatPartitioning partitioning,PetscInt *ncon, int *ierr)
{
CHKFORTRANNULLOBJECT(partitioning);
*ierr = MatPartitioningSetNumberVertexWeights(
	(MatPartitioning)PetscToPointer((partitioning) ),*ncon);
}
#if defined(__cplusplus)
}
#endif
