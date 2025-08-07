#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* matis.c */
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
#define matisgetallowrepeated_ MATISGETALLOWREPEATED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matisgetallowrepeated_ matisgetallowrepeated
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matissetallowrepeated_ MATISSETALLOWREPEATED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matissetallowrepeated_ matissetallowrepeated
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matisstorel2l_ MATISSTOREL2L
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matisstorel2l_ matisstorel2l
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matisfixlocalempty_ MATISFIXLOCALEMPTY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matisfixlocalempty_ matisfixlocalempty
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matissetpreallocation_ MATISSETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matissetpreallocation_ matissetpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matisgetlocalmat_ MATISGETLOCALMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matisgetlocalmat_ matisgetlocalmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matisrestorelocalmat_ MATISRESTORELOCALMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matisrestorelocalmat_ matisrestorelocalmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matissetlocalmattype_ MATISSETLOCALMATTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matissetlocalmattype_ matissetlocalmattype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matissetlocalmat_ MATISSETLOCALMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matissetlocalmat_ matissetlocalmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateis_ MATCREATEIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateis_ matcreateis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matisgetlocaltoglobalmapping_ MATISGETLOCALTOGLOBALMAPPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matisgetlocaltoglobalmapping_ matisgetlocaltoglobalmapping
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matisgetallowrepeated_(Mat A,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatISGetAllowRepeated(
	(Mat)PetscToPointer((A) ),flg);
}
PETSC_EXTERN void  matissetallowrepeated_(Mat A,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatISSetAllowRepeated(
	(Mat)PetscToPointer((A) ),*flg);
}
PETSC_EXTERN void  matisstorel2l_(Mat A,PetscBool *store, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatISStoreL2L(
	(Mat)PetscToPointer((A) ),*store);
}
PETSC_EXTERN void  matisfixlocalempty_(Mat A,PetscBool *fix, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatISFixLocalEmpty(
	(Mat)PetscToPointer((A) ),*fix);
}
PETSC_EXTERN void  matissetpreallocation_(Mat B,PetscInt *d_nz, PetscInt d_nnz[],PetscInt *o_nz, PetscInt o_nnz[], int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLINTEGER(d_nnz);
CHKFORTRANNULLINTEGER(o_nnz);
*ierr = MatISSetPreallocation(
	(Mat)PetscToPointer((B) ),*d_nz,d_nnz,*o_nz,o_nnz);
}
PETSC_EXTERN void  matisgetlocalmat_(Mat mat,Mat *local, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool local_null = !*(void**) local ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(local);
*ierr = MatISGetLocalMat(
	(Mat)PetscToPointer((mat) ),local);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! local_null && !*(void**) local) * (void **) local = (void *)-2;
}
PETSC_EXTERN void  matisrestorelocalmat_(Mat mat,Mat *local, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
PetscBool local_null = !*(void**) local ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(local);
*ierr = MatISRestoreLocalMat(
	(Mat)PetscToPointer((mat) ),local);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! local_null && !*(void**) local) * (void **) local = (void *)-2;
}
PETSC_EXTERN void  matissetlocalmattype_(Mat mat,char *mtype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for mtype */
  FIXCHAR(mtype,cl0,_cltmp0);
*ierr = MatISSetLocalMatType(
	(Mat)PetscToPointer((mat) ),_cltmp0);
  FREECHAR(mtype,_cltmp0);
}
PETSC_EXTERN void  matissetlocalmat_(Mat mat,Mat local, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(local);
*ierr = MatISSetLocalMat(
	(Mat)PetscToPointer((mat) ),
	(Mat)PetscToPointer((local) ));
}
PETSC_EXTERN void  matcreateis_(MPI_Fint * comm,PetscInt *bs,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N,ISLocalToGlobalMapping rmap,ISLocalToGlobalMapping cmap,Mat *A, int *ierr)
{
CHKFORTRANNULLOBJECT(rmap);
CHKFORTRANNULLOBJECT(cmap);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatCreateIS(
	MPI_Comm_f2c(*(comm)),*bs,*m,*n,*M,*N,
	(ISLocalToGlobalMapping)PetscToPointer((rmap) ),
	(ISLocalToGlobalMapping)PetscToPointer((cmap) ),A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
PETSC_EXTERN void  matisgetlocaltoglobalmapping_(Mat A,ISLocalToGlobalMapping *rmapping,ISLocalToGlobalMapping *cmapping, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool rmapping_null = !*(void**) rmapping ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(rmapping);
PetscBool cmapping_null = !*(void**) cmapping ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cmapping);
*ierr = MatISGetLocalToGlobalMapping(
	(Mat)PetscToPointer((A) ),rmapping,cmapping);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! rmapping_null && !*(void**) rmapping) * (void **) rmapping = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cmapping_null && !*(void**) cmapping) * (void **) cmapping = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
