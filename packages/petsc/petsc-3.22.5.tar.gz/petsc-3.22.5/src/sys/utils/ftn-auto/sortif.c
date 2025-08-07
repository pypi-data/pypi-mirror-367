#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* sorti.c */
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

#include "petscsys.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortedint_ PETSCSORTEDINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortedint_ petscsortedint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortedint64_ PETSCSORTEDINT64
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortedint64_ petscsortedint64
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortint_ PETSCSORTINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortint_ petscsortint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortint64_ PETSCSORTINT64
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortint64_ petscsortint64
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortcount_ PETSCSORTCOUNT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortcount_ petscsortcount
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortreverseint_ PETSCSORTREVERSEINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortreverseint_ petscsortreverseint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortedremovedupsint_ PETSCSORTEDREMOVEDUPSINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortedremovedupsint_ petscsortedremovedupsint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortedcheckdupsint_ PETSCSORTEDCHECKDUPSINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortedcheckdupsint_ petscsortedcheckdupsint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortremovedupsint_ PETSCSORTREMOVEDUPSINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortremovedupsint_ petscsortremovedupsint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfindint_ PETSCFINDINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfindint_ petscfindint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsccheckdupsint_ PETSCCHECKDUPSINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsccheckdupsint_ petsccheckdupsint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfindmpiint_ PETSCFINDMPIINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfindmpiint_ petscfindmpiint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortintwitharray_ PETSCSORTINTWITHARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortintwitharray_ petscsortintwitharray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortintwitharraypair_ PETSCSORTINTWITHARRAYPAIR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortintwitharraypair_ petscsortintwitharraypair
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortintwithmpiintarray_ PETSCSORTINTWITHMPIINTARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortintwithmpiintarray_ petscsortintwithmpiintarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortintwithcountarray_ PETSCSORTINTWITHCOUNTARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortintwithcountarray_ petscsortintwithcountarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortintwithintcountarraypair_ PETSCSORTINTWITHINTCOUNTARRAYPAIR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortintwithintcountarraypair_ petscsortintwithintcountarraypair
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortedmpiint_ PETSCSORTEDMPIINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortedmpiint_ petscsortedmpiint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortmpiint_ PETSCSORTMPIINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortmpiint_ petscsortmpiint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortremovedupsmpiint_ PETSCSORTREMOVEDUPSMPIINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortremovedupsmpiint_ petscsortremovedupsmpiint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortmpiintwitharray_ PETSCSORTMPIINTWITHARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortmpiintwitharray_ petscsortmpiintwitharray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortmpiintwithintarray_ PETSCSORTMPIINTWITHINTARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortmpiintwithintarray_ petscsortmpiintwithintarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortintwithscalararray_ PETSCSORTINTWITHSCALARARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortintwithscalararray_ petscsortintwithscalararray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmergeintarray_ PETSCMERGEINTARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmergeintarray_ petscmergeintarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmergeintarraypair_ PETSCMERGEINTARRAYPAIR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmergeintarraypair_ petscmergeintarraypair
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmergempiintarray_ PETSCMERGEMPIINTARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmergempiintarray_ petscmergempiintarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscparallelsortedint_ PETSCPARALLELSORTEDINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscparallelsortedint_ petscparallelsortedint
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscsortedint_(PetscCount *n, PetscInt X[],PetscBool *sorted, int *ierr)
{
CHKFORTRANNULLINTEGER(X);
*ierr = PetscSortedInt(*n,X,sorted);
}
PETSC_EXTERN void  petscsortedint64_(PetscCount *n, PetscInt64 X[],PetscBool *sorted, int *ierr)
{
*ierr = PetscSortedInt64(*n,
	(PetscInt64* )PetscToPointer((X) ),sorted);
}
PETSC_EXTERN void  petscsortint_(PetscCount *n,PetscInt X[], int *ierr)
{
CHKFORTRANNULLINTEGER(X);
*ierr = PetscSortInt(*n,X);
}
PETSC_EXTERN void  petscsortint64_(PetscCount *n,PetscInt64 X[], int *ierr)
{
*ierr = PetscSortInt64(*n,
	(PetscInt64* )PetscToPointer((X) ));
}
PETSC_EXTERN void  petscsortcount_(PetscCount *n,PetscCount X[], int *ierr)
{
*ierr = PetscSortCount(*n,
	(PetscCount* )PetscToPointer((X) ));
}
PETSC_EXTERN void  petscsortreverseint_(PetscCount *n,PetscInt X[], int *ierr)
{
CHKFORTRANNULLINTEGER(X);
*ierr = PetscSortReverseInt(*n,X);
}
PETSC_EXTERN void  petscsortedremovedupsint_(PetscInt *n,PetscInt X[], int *ierr)
{
CHKFORTRANNULLINTEGER(n);
CHKFORTRANNULLINTEGER(X);
*ierr = PetscSortedRemoveDupsInt(n,X);
}
PETSC_EXTERN void  petscsortedcheckdupsint_(PetscCount *n, PetscInt X[],PetscBool *flg, int *ierr)
{
CHKFORTRANNULLINTEGER(X);
*ierr = PetscSortedCheckDupsInt(*n,X,flg);
}
PETSC_EXTERN void  petscsortremovedupsint_(PetscInt *n,PetscInt X[], int *ierr)
{
CHKFORTRANNULLINTEGER(n);
CHKFORTRANNULLINTEGER(X);
*ierr = PetscSortRemoveDupsInt(n,X);
}
PETSC_EXTERN void  petscfindint_(PetscInt *key,PetscCount *n, PetscInt X[],PetscInt *loc, int *ierr)
{
CHKFORTRANNULLINTEGER(X);
CHKFORTRANNULLINTEGER(loc);
*ierr = PetscFindInt(*key,*n,X,loc);
}
PETSC_EXTERN void  petsccheckdupsint_(PetscInt *n, PetscInt X[],PetscBool *dups, int *ierr)
{
CHKFORTRANNULLINTEGER(X);
*ierr = PetscCheckDupsInt(*n,X,dups);
}
PETSC_EXTERN void  petscfindmpiint_(PetscMPIInt *key,PetscCount *n, PetscMPIInt X[],PetscInt *loc, int *ierr)
{
CHKFORTRANNULLINTEGER(loc);
*ierr = PetscFindMPIInt(*key,*n,X,loc);
}
PETSC_EXTERN void  petscsortintwitharray_(PetscCount *n,PetscInt X[],PetscInt Y[], int *ierr)
{
CHKFORTRANNULLINTEGER(X);
CHKFORTRANNULLINTEGER(Y);
*ierr = PetscSortIntWithArray(*n,X,Y);
}
PETSC_EXTERN void  petscsortintwitharraypair_(PetscCount *n,PetscInt X[],PetscInt Y[],PetscInt Z[], int *ierr)
{
CHKFORTRANNULLINTEGER(X);
CHKFORTRANNULLINTEGER(Y);
CHKFORTRANNULLINTEGER(Z);
*ierr = PetscSortIntWithArrayPair(*n,X,Y,Z);
}
PETSC_EXTERN void  petscsortintwithmpiintarray_(PetscCount *n,PetscInt X[],PetscMPIInt Y[], int *ierr)
{
CHKFORTRANNULLINTEGER(X);
*ierr = PetscSortIntWithMPIIntArray(*n,X,Y);
}
PETSC_EXTERN void  petscsortintwithcountarray_(PetscCount *n,PetscInt X[],PetscCount Y[], int *ierr)
{
CHKFORTRANNULLINTEGER(X);
*ierr = PetscSortIntWithCountArray(*n,X,
	(PetscCount* )PetscToPointer((Y) ));
}
PETSC_EXTERN void  petscsortintwithintcountarraypair_(PetscCount *n,PetscInt X[],PetscInt Y[],PetscCount Z[], int *ierr)
{
CHKFORTRANNULLINTEGER(X);
CHKFORTRANNULLINTEGER(Y);
*ierr = PetscSortIntWithIntCountArrayPair(*n,X,Y,
	(PetscCount* )PetscToPointer((Z) ));
}
PETSC_EXTERN void  petscsortedmpiint_(PetscCount *n, PetscMPIInt X[],PetscBool *sorted, int *ierr)
{
*ierr = PetscSortedMPIInt(*n,X,sorted);
}
PETSC_EXTERN void  petscsortmpiint_(PetscCount *n,PetscMPIInt X[], int *ierr)
{
*ierr = PetscSortMPIInt(*n,X);
}
PETSC_EXTERN void  petscsortremovedupsmpiint_(PetscInt *n,PetscMPIInt X[], int *ierr)
{
CHKFORTRANNULLINTEGER(n);
*ierr = PetscSortRemoveDupsMPIInt(n,X);
}
PETSC_EXTERN void  petscsortmpiintwitharray_(PetscCount *n,PetscMPIInt X[],PetscMPIInt Y[], int *ierr)
{
*ierr = PetscSortMPIIntWithArray(*n,X,Y);
}
PETSC_EXTERN void  petscsortmpiintwithintarray_(PetscCount *n,PetscMPIInt X[],PetscInt Y[], int *ierr)
{
CHKFORTRANNULLINTEGER(Y);
*ierr = PetscSortMPIIntWithIntArray(*n,X,Y);
}
PETSC_EXTERN void  petscsortintwithscalararray_(PetscCount *n,PetscInt X[],PetscScalar Y[], int *ierr)
{
CHKFORTRANNULLINTEGER(X);
CHKFORTRANNULLSCALAR(Y);
*ierr = PetscSortIntWithScalarArray(*n,X,Y);
}
PETSC_EXTERN void  petscmergeintarray_(PetscInt *an, PetscInt aI[],PetscInt *bn, PetscInt bI[],PetscInt *n,PetscInt **L, int *ierr)
{
CHKFORTRANNULLINTEGER(aI);
CHKFORTRANNULLINTEGER(bI);
CHKFORTRANNULLINTEGER(n);
CHKFORTRANNULLINTEGER(L);
*ierr = PetscMergeIntArray(*an,aI,*bn,bI,n,L);
}
PETSC_EXTERN void  petscmergeintarraypair_(PetscInt *an, PetscInt aI[], PetscInt aJ[],PetscInt *bn, PetscInt bI[], PetscInt bJ[],PetscInt *n,PetscInt **L,PetscInt **J, int *ierr)
{
CHKFORTRANNULLINTEGER(aI);
CHKFORTRANNULLINTEGER(aJ);
CHKFORTRANNULLINTEGER(bI);
CHKFORTRANNULLINTEGER(bJ);
CHKFORTRANNULLINTEGER(n);
CHKFORTRANNULLINTEGER(L);
CHKFORTRANNULLINTEGER(J);
*ierr = PetscMergeIntArrayPair(*an,aI,aJ,*bn,bI,bJ,n,L,J);
}
PETSC_EXTERN void  petscmergempiintarray_(PetscInt *an, PetscMPIInt aI[],PetscInt *bn, PetscMPIInt bI[],PetscInt *n,PetscMPIInt **L, int *ierr)
{
CHKFORTRANNULLINTEGER(n);
*ierr = PetscMergeMPIIntArray(*an,aI,*bn,bI,n,L);
}
PETSC_EXTERN void  petscparallelsortedint_(MPI_Fint * comm,PetscInt *n, PetscInt keys[],PetscBool *is_sorted, int *ierr)
{
CHKFORTRANNULLINTEGER(keys);
*ierr = PetscParallelSortedInt(
	MPI_Comm_f2c(*(comm)),*n,keys,is_sorted);
}
#if defined(__cplusplus)
}
#endif
