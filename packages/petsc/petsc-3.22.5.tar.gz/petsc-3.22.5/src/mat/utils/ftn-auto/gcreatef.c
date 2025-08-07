#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* gcreate.c */
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
#define matcreate_ MATCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreate_ matcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatefromoptions_ MATCREATEFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatefromoptions_ matcreatefromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseterroriffailure_ MATSETERRORIFFAILURE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseterroriffailure_ matseterroriffailure
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetsizes_ MATSETSIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetsizes_ matsetsizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetfromoptions_ MATSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetfromoptions_ matsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matxaijsetpreallocation_ MATXAIJSETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matxaijsetpreallocation_ matxaijsetpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matheaderreplace_ MATHEADERREPLACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matheaderreplace_ matheaderreplace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matbindtocpu_ MATBINDTOCPU
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matbindtocpu_ matbindtocpu
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matboundtocpu_ MATBOUNDTOCPU
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matboundtocpu_ matboundtocpu
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvaluescoo_ MATSETVALUESCOO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvaluescoo_ matsetvaluescoo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetbindingpropagates_ MATSETBINDINGPROPAGATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetbindingpropagates_ matsetbindingpropagates
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetbindingpropagates_ MATGETBINDINGPROPAGATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetbindingpropagates_ matgetbindingpropagates
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matcreate_(MPI_Fint * comm,Mat *A, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(A);
 PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatCreate(
	MPI_Comm_f2c(*(comm)),A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
PETSC_EXTERN void  matcreatefromoptions_(MPI_Fint * comm, char *prefix,PetscInt *bs,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N,Mat *A, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = MatCreateFromOptions(
	MPI_Comm_f2c(*(comm)),_cltmp0,*bs,*m,*n,*M,*N,A);
  FREECHAR(prefix,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
PETSC_EXTERN void  matseterroriffailure_(Mat mat,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatSetErrorIfFailure(
	(Mat)PetscToPointer((mat) ),*flg);
}
PETSC_EXTERN void  matsetsizes_(Mat A,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatSetSizes(
	(Mat)PetscToPointer((A) ),*m,*n,*M,*N);
}
PETSC_EXTERN void  matsetfromoptions_(Mat B, int *ierr)
{
CHKFORTRANNULLOBJECT(B);
*ierr = MatSetFromOptions(
	(Mat)PetscToPointer((B) ));
}
PETSC_EXTERN void  matxaijsetpreallocation_(Mat A,PetscInt *bs, PetscInt dnnz[], PetscInt onnz[], PetscInt dnnzu[], PetscInt onnzu[], int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLINTEGER(dnnz);
CHKFORTRANNULLINTEGER(onnz);
CHKFORTRANNULLINTEGER(dnnzu);
CHKFORTRANNULLINTEGER(onnzu);
*ierr = MatXAIJSetPreallocation(
	(Mat)PetscToPointer((A) ),*bs,dnnz,onnz,dnnzu,onnzu);
}
PETSC_EXTERN void  matheaderreplace_(Mat A,Mat *C, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool C_null = !*(void**) C ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(C);
*ierr = MatHeaderReplace(
	(Mat)PetscToPointer((A) ),C);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! C_null && !*(void**) C) * (void **) C = (void *)-2;
}
PETSC_EXTERN void  matbindtocpu_(Mat A,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatBindToCPU(
	(Mat)PetscToPointer((A) ),*flg);
}
PETSC_EXTERN void  matboundtocpu_(Mat A,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatBoundToCPU(
	(Mat)PetscToPointer((A) ),flg);
}
PETSC_EXTERN void  matsetvaluescoo_(Mat A, PetscScalar coo_v[],InsertMode *imode, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLSCALAR(coo_v);
*ierr = MatSetValuesCOO(
	(Mat)PetscToPointer((A) ),coo_v,*imode);
}
PETSC_EXTERN void  matsetbindingpropagates_(Mat A,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatSetBindingPropagates(
	(Mat)PetscToPointer((A) ),*flg);
}
PETSC_EXTERN void  matgetbindingpropagates_(Mat A,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatGetBindingPropagates(
	(Mat)PetscToPointer((A) ),flg);
}
#if defined(__cplusplus)
}
#endif
